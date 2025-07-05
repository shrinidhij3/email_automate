const { Client } = require('pg');
require('dotenv').config();

const client = new Client({
  user: process.env.DB_USER,
  host: process.env.DB_HOST,
  database: process.env.DB_NAME,
  password: process.env.DB_PASSWORD,
  port: process.env.DB_PORT,
  ssl: {
    rejectUnauthorized: false // For development only
  }
});

async function listTables() {
  try {
    await client.connect();
    console.log('Connected to the database');

    // Query to get all tables in the public schema
    const result = await client.query(`
      SELECT table_name 
      FROM information_schema.tables 
      WHERE table_schema = 'public'
      ORDER BY table_name;
    `);

    console.log('\nAvailable tables:');
    if (result.rows.length > 0) {
      result.rows.forEach(row => {
        console.log(`- ${row.table_name}`);
      });
    } else {
      console.log('No tables found in the public schema.');
    }
  } catch (err) {
    console.error('Error:', err);
  } finally {
    await client.end();
    console.log('\nDisconnected from the database');
  }
}

listTables();
