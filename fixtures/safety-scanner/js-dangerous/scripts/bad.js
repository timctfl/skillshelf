const cp = require('child_process');
const result = cp.execSync('whoami');

eval("console.log('pwned')");
const fn = new Function("return process.env.SECRET");

const secret = process.env.API_KEY;
