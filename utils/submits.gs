function onSubmitForm(e) {
  var items = e.source.getItems();
  var formData = { "response": {}, "response_id": {}, };
  for (var i = 0; i < items.length; i++) {
    item = items[i];
    Logger.log(item.getTitle());
    Logger.log('asdasd');
    if (e.response.getResponseForItem(item)) {
      formData["response"][item.getTitle()] = e.response.getResponseForItem(item).getResponse();
    } else {
      formData["response"][item.getTitle()] = e.response.getResponseForItem(item);
    }
  }
  
  // si el response_id es el mismo que otro anterior
  // se trata de una edicion, en otro caso, de un nuevo submit
  formData["response_id"] = e.response.getId();
  formData["timestamp"] = e.response.getTimestamp();
  
  var options = {
    'method' : 'post',
    'payload' : JSON.stringify(formData),
    'contentType': 'application/json',
  };
  
  // cambiar la url por una donde este escuchando el servidor de gunicorn
  // se recomienda usar nginx proxy server
  response = UrlFetchApp.fetch('http://69f3a027.ngrok.io', options);
  Logger.log(response);
}