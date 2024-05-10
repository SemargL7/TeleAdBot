import logo from './logo.svg';
import './App.css';
import {useState} from "react";

function App() {
  const [newTest, setNewTest] = useState("TEST MY TEXT")


  function onClickOnText(){
    setNewTest("hi")
  }
  return (
    <div className="App">
      <header className="App-header">
        <img src={logo} className="App-logo" alt="logo" />
        <h1 onClick={onClickOnText}>{newTest}</h1>
        <p>
          Edit <code>src/App.js</code> and save to reload.
        </p>
        <a
          className="App-link"
          href="https://reactjs.org"
          target="_blank"
          rel="noopener noreferrer"
        >
          Learn React
        </a>
      </header>
    </div>
  );
}

export default App;
