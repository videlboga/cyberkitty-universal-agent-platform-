const api_url = 'https://api.amocrm.ru/v4/';
const api_token = 'your_api_token_here';
const clients_list = async () => {
  const response = await fetch(api_url + 'clients.list', {
    method: 'GET',
    headers: {
      'Authorization': 'Bearer ' + api_token
    }
  });
  const data = await response.json();
  return data.items;
};