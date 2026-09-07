// Developer: @SOCIALBANNERR

export default async function handler(req, res) {
  // Enable CORS
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET');

  const { registration_number } = req.query;

  if (!registration_number) {
    return res.status(400).json({
      error: 'Registration number is required',
      developer: '@SOCIALBANNERR'
    });
  }

  try {
    const response = await fetch(
      `https://api-ct.vehicleinfo.app/gw/plt/bffctsvc/api/v1/garage/rc-search?registration_number=${registration_number}`,
      {
        headers: {
          'User-Agent': 'okhttp/4.12.0',
          'Accept': 'application/json, text/plain, */*',
          'authorization': `Bearer ${process.env.AUTH_TOKEN}`,
          'x-user-city-id': '777',
          'super_app_source': 'vehicleinfo_consumerapp',
          'x-api-key': process.env.API_KEY,
          'x_app_instance_id': process.env.APP_INSTANCE_ID,
          'x-device-id': process.env.DEVICE_ID,
          'x-tenant-id': 'VI_INDIA',
          'userid': process.env.USER_ID,
          'x_experiment_id': '252935e1-2b91-4b74-9734-9a40037cd09f',
          'clientid': 'vehicleinfo_consumerapp',
          'appversion': '323',
          'osname': 'android',
          'useragent': 'vehicleinfo_consumerapp/323',
          'source': 'MobileApp',
          'x_country': 'IN',
          'x-tenant-slug': 'vehicleinfo'
        }
      }
    );

    const data = await response.json();
    
    res.status(200).json({
      ...data,
      developer: '@SOCIALBANNERR'
    });
    
  } catch (error) {
    res.status(500).json({
      error: 'Internal server error',
      message: error.message,
      developer: '@SOCIALBANNERR'
    });
  }
}
