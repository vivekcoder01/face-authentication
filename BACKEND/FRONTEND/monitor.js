setInterval(() => {
  fetch("/monitor")
    .then(response => response.json())
    .then(data => console.log("Monitoring:", data));
}, 5000);
