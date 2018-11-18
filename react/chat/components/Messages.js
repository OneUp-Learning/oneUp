import React, {Component} from "react";
import PropTypes from "prop-types";

import Message from './Message';

import Grid from 'react-md/lib/Grids/Grid';
import Cell from 'react-md/lib/Grids/Cell';

class Messages extends Component{
  static propTypes = {
    mobile: PropTypes.bool.isRequired,
    messages: PropTypes.array.isRequired
  };
  render(){
    
    return(
      !this.props.messages.length ? (
        <Grid>
          <Cell size={12}>
          <h1>Be the first to say something!</h1>
          </Cell>
        </Grid>
      ) : (
        this.props.messages.map((message, index) => <Message key={index} data={message} mobile={this.props.mobile} />)   
    ));
  }
}
export default (Messages);