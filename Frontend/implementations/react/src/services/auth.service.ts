import axios from "axios";
import { Buffer } from "buffer";

const cognito_domain = process.env.cognito_domain
const client_id_cog=process.env.client_id_cog
const client_secret_cog=process.env.client_secret_cog
const callback_uri_cog=process.env.callback_uri_cog

const encode = (str: string):string => Buffer.from(str, 'binary').toString('base64');


class AuthService {
  

  logout() {
    sessionStorage.removeItem("user");
  }
  
  getSecretToken()
  {
    return process.env.sec_token
  }
  
  
  isValidSession()
  {
    if(sessionStorage.getItem("user"))
    {
      return true
    }
    else
    {
      return false
    }
  }
  
  async getBearerToken(authcode: string)
  {
    var authorization =encode(client_id_cog+":"+client_secret_cog)
    const headers = {
    headers: { Authorization: "Basic "+authorization,
               'Content-Type': 'application/x-www-form-urlencoded'
             }
    };
    const bodyParameters = {
       grant_type: "authorization_code",
       code: authcode,
       redirect_uri: callback_uri_cog,
       client_id:client_id_cog
    };
    
    var access_token=''
    const body = `grant_type=authorization_code&client_id=${client_id_cog}&code=${authcode}&redirect_uri=${callback_uri_cog}`  
    try {
      const response=await axios.post( 
        cognito_domain+'/oauth2/token',
        body,
        headers
      )
      access_token=response.data.access_token
      
    }catch (err) {  
  		console.log("Unable to get access token "+err.response.data.error)  
  		 
	  }  
	  return access_token
  }
    
  

  async getCurrentUser(authcode: string) {
    
    
	  var access_token= await this.getBearerToken(authcode)
	  const config_token = {  
  		headers: {  
  			Authorization: `Bearer ${access_token}`  
  		}  
  	}  
  	const response = await axios.get(`${cognito_domain}/oauth2/userInfo`, config_token)  
  	const user = response.data.email
  	
  	console.log("found user"+ user)
  	sessionStorage.setItem("user",user)
    return user;
  }
}

export default new AuthService();