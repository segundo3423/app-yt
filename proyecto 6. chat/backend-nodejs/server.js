const express = require('express');
const cors = require('cors');
const path = require('path');

const app = express();
const PORT = 3000;

// Middleware
app.use(cors());
app.use(express.json());
app.use(express.static(path.join(__dirname, '../frontend')));
app.use('/assets', express.static(path.join(__dirname, '../frontend/assets')));

// Rutas

app.listen(PORT, () => {
    console.log(`Servidor escuchando en puerto ${PORT}`);
});
