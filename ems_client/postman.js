// Post-request ***********
const jsonData = pm.response.json();
const token = jsonData.access_token.split('.')[1];
const decodedToken = JSON.parse(Buffer.from(token, 'base64').toString('utf-8'));

// Store the access token, refresh token, and expiration time in environment variables
pm.environment.set("accessToken", jsonData.access_token);
pm.environment.set("refreshToken", jsonData.refresh_token);
pm.environment.set("accessTokenExp", decodedToken.exp);

// Pre-request ***********
const accessTokenExpiry = pm.environment.get("accessTokenExp");
const refreshToken = pm.environment.get("refreshToken")
const currentTime = Math.floor(Date.now() / 1000); // Current time in seconds

if (currentTime >= accessTokenExpiry) {
    // Access token has expired, refresh it using the refresh token
    pm.sendRequest({
        url: 'localhost:8000/api/v1/auth/refresh',
        method: 'POST',
        header: {
            'Content-Type': 'application/json'
        },
        body: {
            mode: 'raw',
            raw: JSON.stringify({
                "token": refreshToken
            })
        }
    }, function (err, res) {
        if (res && res.code === 200) {
            const jsonData = res.json();

            // Save the new access token and its expiration time
            const newToken = jsonData.access_token.split('.')[1];
            const decodedNewToken = JSON.parse(Buffer.from(newToken, 'base64').toString('utf-8'));

            pm.environment.set("accessToken", jsonData.access_token);
            pm.environment.set("accessTokenExp", decodedNewToken.exp);
        } else {
            console.log("Failed to refresh token", err);
        }
    });
} else {
    console.log("Access token is still valid.");
}