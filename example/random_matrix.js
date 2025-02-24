const math = require('mathjs');

function handle(args) {
  const { lines, cols } = args;

  const matrix = Array.from({ length: lines }, () => 
    Array.from({ length: cols }, () => math.randomInt(1, 100))
  );
  
  return matrix;
}

module.exports = { handle };