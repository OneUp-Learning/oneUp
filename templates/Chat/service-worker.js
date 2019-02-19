function windowClient(url) {
    return clients.matchAll({ type: 'window', includeUncontrolled: true }).then(function(windowClients) {
      let matchingClient = null;
      console.log(windowClients);
      for (let i = 0; i < windowClients.length; i++) {
        const windowClient = windowClients[i];
        if (windowClient.url === url) {
          matchingClient = windowClient;
          break;
        }
      }

      if (matchingClient) {
        return matchingClient;
      } else {
        return Promise.reject("No clients");
      }
    });
  }


self.addEventListener("activate", event => {
  event.waitUntil(clients.claim());
});

// The first time the user starts up the PWA, 'install' is triggered.
self.addEventListener('install', function(event) {
  event.waitUntil(skipWaiting());
});

// When the webpage goes to fetch files, we intercept that request and serve up the matching files
// if we have them
self.addEventListener('fetch', function(event) {
});

self.addEventListener('notificationclick', function(event) {
  var notification = event.notification;
  console.log(notification);
  notification.close();

  if (!notification.data.hasOwnProperty('options'))
      return;

  var options = notification.data.options;

  var promise = Promise.resolve();

  if (options.action == 'message') {
        promise = promise.then(function(){ return windowClient(options.url);})
        .then(function(client) {
          if(event.reply){
           client.postMessage({msg: event.reply, user: options.user});
           
          } else {
            client.focus();
          }
            return;
        });
  }
  else if (options.action == 'default') {
      promise =
          promise.then(function() { return windowClient(options.url); })
                  .then(function(client) { return client.focus(); })
                  .catch(function() { clients.openWindow(options.url); });
  }

  event.waitUntil(promise);
});
