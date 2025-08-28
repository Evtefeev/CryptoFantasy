self.addEventListener("install", event => {
  self.skipWaiting();
});

self.addEventListener("fetch", event => {
  if (event.request.destination === "image") {
    event.respondWith(
      caches.match(event.request).then(resp => {
        return resp || fetch(event.request).then(response => {
          return caches.open("images-cache").then(cache => {
            cache.put(event.request, response.clone());
            return response;
          });
        });
      })
    );
  }
});
