import React from 'react';
import Generator from './Generator.js';

export default class App extends React.Component {
  render() {
    return (
      <div>
          <Generator url="http://127.0.0.1:8000/api/inputtest/"/>
      </div>
    );
  }
}

  