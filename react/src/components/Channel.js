import React, { Component } from "react";
import PropTypes from "prop-types";

import Form from './Form';
import Messages from "./Messages";

import Grid from 'react-md/lib/Grids/Grid';
import Cell from 'react-md/lib/Grids/Cell';
import Toolbar from 'react-md/lib/Toolbars/Toolbar';
import ReactResizeDetector from 'react-resize-detector';

import './socket.js';
import '../css/spinner.css';

class Channel extends Component {

  constructor(props){
    super(props);
    this.state = {
      data: [],
      loaded: false,
      placeholder: "Loading...",
      page: 2,
      channel: props.channel,
      channelAccess: props.channelAccess,
      scrollBoxHeight: 'calc(100vh - 144px)',
      messageBoxHeight: '72px',
      prevScrollHeight: null,
      loadedAllMessages: false,
    }
    this.scroll = React.createRef();
  }
  static propTypes = {
    mediaClass: PropTypes.string,
    channelAccess: PropTypes.bool.isRequired,
    channel: PropTypes.object.isRequired,
    endpoint: PropTypes.string.isRequired,
    user: PropTypes.object.isRequired,
    isTeacher: PropTypes.bool.isRequired,
    course: PropTypes.object.isRequired,
    studentAvatars: PropTypes.object.isRequired,
    joinCallback: PropTypes.func.isRequired,
    leaveCallback: PropTypes.func.isRequired
  };

  loadMoreMessages = () => {
    var url = this.props.endpoint+""+this.state.page;
    console.log(url);
    return fetch(url).then(response => {
      return response.json();
    }).then(messages =>{
      if(Object.keys(messages).length != 0){
        this.setState(prevState => ({
          data: prevState.data.concat(messages),
          page: prevState.page + 1
        }));
      } else {
        this.setState({loadedAllMessages: true});
      }
    })
  }
  scrollToElement(){
    if(this.scroll){
      this.scroll.scrollTo(0, this.scroll.scrollHeight);
    }
  }
  handleScroll(e){
    if(e.target.scrollTop <= 0 && this.state.loadedAllMessages == false){
      this.setState({prevScrollHeight: e.target.scrollHeight}, () => {
        this.loadMoreMessages().then(data => {
          this.scroll.scrollTo(0, this.scroll.scrollHeight - this.state.prevScrollHeight);
        });      
      });
      
    }
  }
  onResize(width, height){
    this.setState({scrollBoxHeight: "calc(100vh - "+(height)+"px)", messageBoxHeight: height+'px'});
  }
  getCurrentNotification(registration) {
        return registration.getNotifications()
        .then(notifications => {
          let currentNotification = null;
    
          for(let i = 0; i < notifications.length; i++) {
            if (notifications[i].data && 
                notifications[i].tag === this.props.channel.channel_name &&
              notifications[i].data.user !== this.props.user.id) {
              currentNotification = notifications[i];
              //console.log(currentNotification);
              return currentNotification;
            }
          }
    
          return currentNotification;
        })
  }
  notify(message){
      if (Notification.permission == 'granted') {
        navigator.serviceWorker.getRegistration().then((reg) => {
            if(!document.hasFocus()){
              //console.log("Notify");
              this.getCurrentNotification(reg).then((currentNotification) => {
                var options = {
                  tag: this.props.channel.channel_name,
                  body: message.message.message,
                  icon: this.props.studentAvatars[message.user.id]['avatar'],
                  badge: '/static/images/ic_stat_chat.png',
                  timestamp: Date.now(),
                  renotify: true,
                  actions: [
                      {action: 'message', title: 'Reply', type:'text',
                        },

                    ],
                  data: {
                      options: {
                          action: 'message',
                          close: 'true',
                          url: document.location.toString(),
                          user: this.props.user.id
                      },
                  }
                };
          
                let title = ' • #' + message.message.channel.channel_name;
                return reg.showNotification(title, options);
              });
            }
          });
          
      }
  }

  componentDidMount() {
    chat_socket.onopen = function(){
      //console.log("Connected to chat socket: ");
    }
    chat_socket.onclose = function(){
      //console.log("Disconnected from chat socket: ");
    }
    chat_socket.onmessage = function(m){
      var message = JSON.parse(m.data);
      //console.log(message);
      if(message.event == 'message_channel'){
        this.setState(prevState => ({
          data: [message.message, ...prevState.data]
        }))
        if(this.props.user.id !== message.user.id){
          if(message.channel_name != this.props.channel.channel_name)
            return;
          this.notify(message);
        }
      }
      else if(message.event == 'join_channel'){
        if(message.channel_name != this.props.channel.channel_name)
          return;

        if(this.props.user.id == message.user.id){
          this.props.joinCallback(message.channel_name);
          //console.log("You Join");
        } else {
          //console.log("Someone Join")
          this.props.leaveCallback(false);
        }
      }
      else if(message.event == 'change_topic'){
        if(message.channel_name != this.props.channel.channel_name)
          return;

        if(this.props.user.id == message.user.id){
          this.props.leaveCallback(false);
          //console.log("You Change Topic");
        } else {
          //console.log("Someone Change Topic")
          this.props.leaveCallback(false);
        }
      }
      else if(message.event == 'leave_channel' ){
         if(message.channel_name != this.props.channel.channel_name)
          return;
          
        if(this.props.user.id == message.user.id){
          this.props.leaveCallback(true);
          //console.log("You Leave")
        } else {
          //console.log("Someone Left")
          this.props.leaveCallback(false);
        }
      }
      else if(message.event == 'delete_channel'){
       
        if(this.props.channel){
          if(this.props.channel.channel_name == message.channel_name && this.props.user.id == message.user.id){
            //console.log("You Deleted Channel")
            this.props.leaveCallback(true);
          }
          else{
            //console.log("Somone Delete Channel")
            this.props.leaveCallback(false);
          }
        }
      }
      else if(message.event == 'add_channel'){
       
        if(this.props.user.id != message.user.id){
          //console.log("Someone Add Channel")
          this.props.leaveCallback(false);
        }
        else{
          //console.log("You Add Channel")
        }

      }
    }.bind(this)

    fetch(this.props.endpoint+"1")
      .then(response => {
        if (response.status !== 200) {
          return this.setState({ placeholder: "Something went wrong" });
        }
        return response.json();
      })
      .then(data => {
        this.setState({ data: data, loaded: true }); 
        //console.log(data);
        this.scrollToElement();
      });
  }
  render() {
    const { data, loaded, placeholder, channel, channelAccess, scrollBoxHeight, messageBoxHeight } = this.state;
    const messagesContainer = {
      bottom: '0%',
      overflow: 'auto',
      height: scrollBoxHeight,
    }
    const scrollBox = {
      paddingLeft: '0px',
      paddingRight: '0px',
      paddingTop: '0px',
      paddingBottom: messageBoxHeight,
      minHeight: scrollBoxHeight
    }
    const messageBox = {
      top: 'auto',
      bottom: '0',
      height: 'auto',
      maxHeight: '40%',
    }
    const flexBox = {
      display: 'flex',
      flexFow: 'column',
      flexDirection: 'column-reverse',
      alignItems: 'flex-end'
    }
    return (loaded) ? (   
      <div> 
        <div ref={(el) =>{this.scroll= el;}} style={messagesContainer} onScroll={(e) => {this.handleScroll(e)}}>    
          <Grid style={scrollBox}>
            <Cell size={12} style={flexBox}><Messages messages={data} isTeacher={this.props.isTeacher} user={this.props.user} studentAvatars={this.props.studentAvatars} mobile={this.props.mediaClass == ''} /></Cell>
          </Grid>
        </div>
        <ReactResizeDetector handleHeight resizableElementId={'2'} onResize={(width, height) => this.onResize(width, height)}/>
        <Toolbar id={'2'} fixed={true} style={messageBox} themed={true} title={<Form className={'md-title md-title--toolbar '+this.props.mediaClass} mediaClass={this.props.mediaClass} disable={!channelAccess} channel={channel} user={this.props.user} course={this.props.course} scrollCallback={() => this.scrollToElement()} />} />
      </div>
      ) : ( <div className={"loader"}>
      <svg viewBox="0 0 32 32" width="32" height="32">
        <circle id="spinner" cx="16" cy="16" r="14" fill="none"></circle>
      </svg>
    </div>);
  }
}
export default Channel;
