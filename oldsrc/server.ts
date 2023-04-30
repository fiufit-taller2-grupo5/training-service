// src/server.ts
import 'reflect-metadata';
import morgan from 'morgan';
import { createApp } from './app';

const port = process.env.PORT || 80;
const app = createApp();

app.use(morgan('common'));

app.get('/health', (_, res) => {
  res.status(200).send({
    status: 'ok',
  });
});

// in case of not found
app.get('*', (_, res) => {
  res.status(404).send('not found');
});

app.listen(port, () =>
  console.log(`Example app listening at http://localhost:${port}`)
);
