# Requirements

npm install -g firebase-tools
npm i firebase-admin csv-parse

THIS IS FOR SETTING UP THE CREDENTIALS

```
setx GOOGLE_APPLICATION_CREDENTIALS "C:\Users\MSI\Desktop\Alex\PoliciApp\Firebase\service-account.json"

$env:GOOGLE_APPLICATION_CREDENTIALS = "C:\Users\MSI\Desktop\Alex\PoliciApp\Firebase\service-account.json"
```

# Starting theemulator

Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass

firebase emulators:start --only firestore

after that 

node import.js