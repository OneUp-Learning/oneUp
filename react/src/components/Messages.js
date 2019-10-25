import React, {Component} from "react";
import PropTypes from "prop-types";

import Message from './Message';
import TimestampMessage from './TimestampMessage';

import Grid from 'react-md/lib/Grids/Grid';
import Cell from 'react-md/lib/Grids/Cell';
const moment = require('moment');

class Messages extends Component{
  static propTypes = {
    mobile: PropTypes.bool.isRequired,
    isTeacher: PropTypes.bool.isRequired,
    user: PropTypes.object.isRequired,
    studentAvatars: PropTypes.object.isRequired,
    messages: PropTypes.array.isRequired
  };
  constructor(props){
    super(props);
    this.state = {
      messages: this.props.messages,
    };
  }
  componentDidMount() {
    this.processMessages();
  }

  componentDidUpdate(prevProps) {
    
    if (prevProps.messages !== this.props.messages) {
      this.processMessages();
      this.setState({messages: this.props.messages})
    }

  }
  clearTimestamps(){
    for(var index = this.props.messages.length-1; index >= 0; index--){
      let message = this.props.messages[index];
      if('type' in message){
        if(message['type'] == 'timestamp'){
          this.props.messages.splice(index, 1)
        }
      }
    }
  }
  processMessages(){

    if(this.props.messages.length > 0){
      this.clearTimestamps();
      const today = moment().endOf('day')
      const yesterday = moment().subtract(1, 'days').endOf('day')
      let latest_date = moment(this.props.messages[0]['timestamp']).endOf('day')

      for(var index = 0; index < this.props.messages.length; index++){
        let message = this.props.messages[index];

        let message_timestamp = moment(message['timestamp']);
        if(message_timestamp <= latest_date.clone().subtract(1, 'days').endOf('day')){
         
          let info = {'type': 'timestamp', 'value': 'Unknown'}
          if(latest_date.format('MMMM Do, YYYY') == today.format('MMMM Do, YYYY')){
            info['value'] = 'Today'
          }
          else if(latest_date.format('MMMM Do, YYYY') == yesterday.format('MMMM Do, YYYY')){
            info['value'] = 'Yesterday'
          } else {
            info['value'] = latest_date.format('MMMM Do, YYYY')
          }
          this.props.messages.splice(index, 0, info)
          latest_date = message_timestamp.endOf('day');
        }
       
      }
      let message_timestamp = moment(this.props.messages[this.props.messages.length-1]['timestamp']).endOf('day').format('MMMM Do, YYYY');
      let info = {'type': 'timestamp', 'value': 'Unknown'}
      if(message_timestamp == today.format('MMMM Do, YYYY')){
        info['value'] = 'Today'
      }
      else if(message_timestamp == yesterday.format('MMMM Do, YYYY')){
        info['value'] = 'Yesterday'
      } else {
        info['value'] = message_timestamp
      }
      this.props.messages.push(info)
    }
  }
  render(){
    
    return(
      !this.props.messages.length ? (
        <Grid>
          <Cell size={12}>
          <h1>Be the first to say something!</h1>
          </Cell>
        </Grid>
      ) : (
        this.props.messages.map((message, index) => {
          if('type' in message){
            return <TimestampMessage key={index} data={message} mobile={this.props.mobile} />
          } else {
            return <Message key={index} data={message} isTeacher={this.props.isTeacher} user={this.props.user} studentAvatars={this.props.studentAvatars} mobile={this.props.mobile} />
          }
      })   
    ));
  }
}
export default (Messages);