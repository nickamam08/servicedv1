require('dotenv').config();
const { Client } = require('pg');

const client = new Client({
  user: process.env.DB_USER,
  host: process.env.DB_HOST,
  database: process.env.DB_NAME,
  password: process.env.DB_PASSWORD,
  port: process.env.DB_PORT,
});

async function testConnection() {
  try {
    console.log('⏳ Intentando conectar a PostgreSQL...');
    await client.connect();
    console.log('✅ ¡Conexión exitosa!');
    
    const res = await client.query('SELECT NOW()');
    console.log('🕒 Hora del servidor:', res.rows[0].now);
    
    console.log('\n📋 Tablas en la base de datos:');
    const tables = await client.query(`
      SELECT table_name 
      FROM information_schema.tables 
      WHERE table_schema = 'public' 
      ORDER BY table_name;
    `);
    
    if (tables.rows.length === 0) {
      console.log('⚠️ No se encontraron tablas (¿Ya ejecutaste schema.sql?)');
    } else {
        tables.rows.forEach(row => {
            console.log(` - ${row.table_name}`);
        });
    }

    await client.end();
  } catch (err) {
    console.error('❌ Error de conexión:', err.message);
    console.error('🔍 Verifica tus credenciales en el archivo .env');
    if (err.code === '28P01') {
        console.error('💡 Pista: Error de autenticación (contraseña incorrecta).');
    } else if (err.code === '3D000') {
      console.error(`💡 Pista: La base de datos "${process.env.DB_NAME}" no existe.`);
    } else if (err.code === 'ECONNREFUSED') {
      console.error('💡 Pista: ¿Está PostgreSQL ejecutándose en el puerto ' + process.env.DB_PORT + '?');
    }
    
    // Ensure process exits for scripts
    process.exit(1); 
  }
}

testConnection();
