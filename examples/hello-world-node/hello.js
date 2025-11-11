#!/usr/bin/env node

const axios = require('axios');

const API = 'http://localhost:31415';

async function main() {
  try {
    await axios.post(`${API}/showtoast`, {
      text: 'Hello from your first Node.js plugin!',
      iconType: 2,
      priority: 5,
      durationSeconds: 5
    });
    
    console.log('Plugin executed successfully!');
  } catch (error) {
    console.error('Error:', error.message);
  }
}

main();
