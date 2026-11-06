# LONGTUA Mobile

The mobile application for LONGTUA, built with Expo Router and React Native.

## Run locally

Install dependencies and start Expo:

```powershell
npm install
$env:EXPO_PUBLIC_API_BASE_URL="http://<BACKEND-LAN-IP>:8000/api"
npx expo start
```

For Expo Go on an iPhone, replace `<BACKEND-LAN-IP>` with the IPv4 address of
the computer running the backend. The phone and computer must use the same
Wi-Fi network.

The backend must listen on the network interface:

```powershell
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

## Current mobile flow

1. Sign in with an existing verified account.
2. View the current confirmed schedule.
3. View activities that are not scheduled.
4. Create or cancel an activity.
5. Submit a planning request and review its proposal.
6. Confirm or reject the proposal.
7. Manage account and planner settings from the Settings tab.

## Validation

```powershell
npx tsc --noEmit
```

The mobile app uses the API contract under `/api`. It does not contain a
separate presentation-only data source.
