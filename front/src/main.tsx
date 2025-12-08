import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
// import App from './App.tsx'
import "@radix-ui/themes/styles.css";
import {Body} from "./layout/body.tsx";

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <Body />
  </StrictMode>,
)
