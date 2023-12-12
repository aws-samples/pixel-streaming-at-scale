import { Component } from "react";

export default class Start extends Component {
  
  componentDidMount() {
    //window.location.href="https://metaverseloginpool.auth.ap-south-1.amazoncognito.com/oauth2/authorize?client_id=5s3a1a5q00v4dlur6c9na95ej6&response_type=code&scope=aws.cognito.signin.user.admin+email+openid&redirect_uri=https%3A%2F%2Fd29rttxscxdopy.cloudfront.net"
  }

  componentWillUnmount() {
    //window.location.reload();
  }

  render() {
    
      return (
        <div>Please sign in  again !</div>
      );
    
  }
}