const fs = require('node-fs');

fs.copy('src/static', 'build/static', (err) => {
  if (err) {
    console.error(err);
  } else {
    console.log('Files copied successfully!');
  }
});