import React from 'react';
import { Toaster } from 'react-hot-toast';
import '../styles/globals.css';

export default function App({ Component, pageProps }) {
  return (
    <>
      <Component {...pageProps} />
      <Toaster
        position="top-right"
        toastOptions={{
          style: {
            background: '#ffffff',
            color: '#111827',
            border: '1px solid rgba(0,0,0,0.1)',
            fontSize: '13px',
            borderRadius: '8px',
            padding: '12px 16px'
          },
        }}
      />
    </>
  );
}
