// Copyright Epic Games, Inc. All Rights Reserved.

const { merge } = require('webpack-merge');
const common = require('./webpack.common.js');
const path = require('path');
const webpack = require("webpack");
 //Start : AWS - allowed usage of  environment variables
require('dotenv').config();
//End : AWS - allowed usage of  environment variables

module.exports = merge(common, {
    //Start : AWS - allowed usage of  environment variables
    plugins: [
        new webpack.DefinePlugin({
            
            // Refer cloudformation output : Client ID for Cognito (CognitoClientID)
            'process.env.client_id_cog': JSON.stringify(''),
            // Refer cloudformation output : Domain URL for Cognito (CognitoDomainURL)
            'process.env.cognito_domain': JSON.stringify(''),
            // This information is not available in CloudFromation. Please navigate to AWS Console->Cognito. Click on user pool 'ueauthenticationpool'
            // Click on App Integration tab and scroll down to App client list. Click on App Client Name
            // You should be able to retrieve the client secret from the App client information widget by toggling the
            // show client secret button
            'process.env.client_secret_cog': JSON.stringify(''),
            // Refer cloudformation output : Callback URL for Cognito (CognitoCallBackURL)
            'process.env.callback_uri_cog': JSON.stringify(''),
            // Refer cloudformation output : Web socket endpoint for api server (APIGatewayWSAPI)
            'process.env.api_ws': JSON.stringify(''),
            // Refer cloudformation output : Web socket endpoint for signalling server (SignallingServerWSAPI)
            'process.env.sig_ws': JSON.stringify(''),
            // No need to change this. If you modify, make sure you also update clientSecret environment variable for requestSession lambda
            'process.env.sec_token': JSON.stringify(''),
            
            
    })
  ],
  //End : AWS - allowed usage of  environment variables
    mode: 'development',
    devtool: 'inline-source-map'
});
