const express = require('express');
const app = express();
app.get('/', (req, res) => {
  res.send('Welcome to my Express server!');
});
app.listen(3000, () => {
  console.log('Server started on port 3000');
});