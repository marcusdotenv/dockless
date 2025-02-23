const express = require('express');
const bodyParser = require('body-parser');
const { handle } = require('./function'); 

const app = express();
const port = 8001;

app.use(bodyParser.json());

app.get('/', (req, res) => {
  res.json({ up: true });
});

app.post('/execute', (req, res) => {
  console.log("Starting executing function...");
  const body = req.body;
  
  try {
    const result = handle(body);
    console.log("Finishing executing function...");
    res.json(result); 
  } catch (error) {
    console.error("Error executing function:", error);
    res.status(500).json({ error: "Erro ao executar a função" });
  }
});

app.listen(port, () => {
  console.log(`Running at port ${port}`);
});
