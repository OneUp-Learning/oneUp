import React, { Component } from "react";
import ReactDOM from "react-dom";

import Channel from "./Channel";

import NavigationDrawer from 'react-md/lib/NavigationDrawers/NavigationDrawer';
import Autocomplete from 'react-md/lib/Autocompletes/Autocomplete';
import FontIcon from 'react-md/lib/FontIcons/FontIcon';
import Grid from 'react-md/lib/Grids/Grid';
import Cell from 'react-md/lib/Grids/Cell';
import Button from 'react-md/lib/Buttons/Button';
import TextField from 'react-md/lib/TextFields/TextField';
import DialogContainer from 'react-md/lib/Dialogs/DialogContainer';
import MenuButton from 'react-md/lib/Menus/MenuButton';
import List from 'react-md/lib/Lists/List';
import ListItem from 'react-md/lib/Lists/ListItem';
import Avatar from 'react-md/lib/Avatars/Avatar';
import Layover from 'react-md/lib/Helpers/Layover';

import './socket.js';
import '../css/spinner.css';

function get_cookie(name) {
    var value;
    if (document.cookie && document.cookie !== '') {
        document.cookie.split(';').forEach(function (c) {
            var m = c.trim().match(/(\w+)=(.*)/);
            if(m !== undefined && m[1] == name) {
                value = decodeURIComponent(m[2]);
            }
        });
    }
    return value;
}

class App extends Component{
    constructor(props){
        super(props);
        this.state = {
            channels: [],
            subscribedChannels: [],
            channelSelected: false,
            channelAccess: false,
            activeChannel: null,
            user: null,
            isLoading: true,
            showCreateChannelDialog: false,
            showDeleteChannelDialog: false,
            showChannelUsersDialog: false,
            showChannelTopicDialog: false,
            newChannelName: '',
            newChannelTopic: '',
            changeChannelTopic: '',
            createChannelNameError: '',
            createChannelTopicError: '',
            changeChannelTopicError: '',
            createChannelNameErrorState: false,
            createChannelTopicErrorState: false,
            changeChannelTopicErrorState: false,
            autocompleteValue: '',
            lastChannelIndex: 1,
            navItems: [
                {
                    key:"channels-header",
                    subheader: true,
                    primaryText: "Subscribed Channels",
                },
                {
                    key: 'create-channel',
                    primaryText: 'Create Channel',
                    rightIcon: <FontIcon key={"create-channel-icon"} primary>add_circle</FontIcon>,
                    onClick: (e) => this.onOpenCreateChannelDialog(),
                },
                { key: 'divider', divider: true }, 
                {
                    key: 'logout', 
                    primaryText:'Log out',
                    leftIcon: <FontIcon>keyboard_arrow_left</FontIcon>,
                    onClick: (e) => this.onLogOut()
                }

            ],
            mediaClass: '',
        }

    }
    
    createNavItem(prevState, data){
        let items = [];
        let lastChannelIndex = this.state.lastChannelIndex;
        const activeListItemStyle = {
            backgroundColor: '#673ab71c'
        }
        // console.log("Old")
        // console.log(prevState);

        // console.log("New")
        // console.log(data);
        for(var id in Object.entries(data)){
            let channel = data[id];
            let found = prevState.filter(obj => {
                return obj.channel_name === channel.channel_name
            })[0];
            if(!found){
                items.push({key: channel.channel_name,
                            active: this.state.activeChannel ? this.state.activeChannel.channel_name === channel.channel_name : false,
                            activeBoxStyle: activeListItemStyle,
                            leftIcon: <FontIcon key={channel.channel_name+"-icon"}>people</FontIcon>,
                            onClick: (e) => this.onSelectedChannel(e, channel.channel_name, channel.channel_url),
                            primaryText: '# '+channel.channel_name,
                            channel_name: channel.channel_name
                })
            }
            else {
                for(let index = prevState.length-1; index > 0; index--){
                    let c = prevState[index];
                    if(channel.channel_name == c.channel_name){
                        prevState.splice(index, 1);
                    }
                }
            }
        }
        const navItems = this.state.navItems;
        if(prevState.length > 0){
            for(var i = prevState.length-1; i > 0; i--){
                let c = prevState[i];
                for(var index = navItems.length-1; index > 0; index--){
                    let channel = navItems[index];
                    if (channel.divider || channel.subheader || channel.key == 'logout' || channel.key == 'create-channel')
                        continue;

                    if(channel.key == c.channel_name){
                        navItems.splice(index, 1);
                        lastChannelIndex--;
                        break;
                    }
                }
                prevState.splice(i, 1);
            }
        }
        navItems.splice(lastChannelIndex, 0, ...items);
        lastChannelIndex += items.length;
        return [navItems, lastChannelIndex];
    }
    fetchChannels(){
        return fetch(window.location.href+'api/channels')
        .then(response => {
            if (response.status !== 200) {
                return this.setState({ placeholder: "Something went wrong" });
            }
            return response.json();
        })
        .then(data => {
            //console.log(data);
            let items = this.createNavItem(this.state.subscribedChannels, data.subscribed_channels);
            if(items[0][items[1]+2].key != 'user'){
                items[0].splice(items[1]+2, 0, {
                    key: 'user', 
                    primaryText: this.state.user.username,
                    secondaryText: this.state.user.first_name + ' ' + this.state.user.last_name,
                    leftAvatar: <Avatar style={{border: 'none', borderRadius: '10%'}} src={'https://avatars.io/instagram/'+this.state.user.username} />,
                })
            }
            
            this.setState({channels: data.all_channels, subscribedChannels: data.subscribed_channels, navItems: items[0], lastChannelIndex: items[1], isLoading: false }); 
        })
    }
    getChannelObject(channel_name){
        let channels = this.state.channels
        for(var id in Object.entries(channels)){
            let channel = channels[id];
            if(channel.channel_name == channel_name)
                return channel
        }
        return null;
    }
    isChannelSubscribed(channel_name){
        let subscribed_channels = this.state.subscribedChannels;
        for(var id in Object.entries(subscribed_channels)){
            let channel = subscribed_channels[id];
            if(channel.channel_name == channel_name){
                return true;
            }
        }
        return false;
    }
    fetchUser(){
        return fetch(window.location.href+'api/user')
        .then(response => {
            if (response.status !== 200) {
                return this.setState({ placeholder: "User not found" });
            }
            return response.json();
        })
        .then(data => {
            //console.log(data);
            this.setState({user: data}); 
        });
    }
    onLogOut(e){
        fetch('../api/user')
        .then(response => {
            if (response.status !== 200) {
                return this.setState({ placeholder: "User not found" });
            }
            return response.json();
        })
        .then(data => {
            //console.log(data);
            window.location.href = '../home';
        });
    }
    onSelectedChannel(e, channel_name, channel_url){
        const navItems = this.state.navItems;
        let selectedChannel = null;

        for(var index = 0; index < navItems.length; index++){
            let channel = navItems[index];

            if (channel.divider || channel.subheader || channel.key == 'logout' || channel.key == 'create-channel')
                continue;

            if(channel.key == channel_name){
                channel.active = !channel.active;
                selectedChannel = channel;
                continue;
            }
            channel.active = false;
        }
        if(selectedChannel){
            if(selectedChannel.active)
                change_socket(channel_url+'/');
            else
                change_socket("generic/");
            this.setState(prevState => ({navItems: navItems, activeChannel: this.getChannelObject(channel_name), channelSelected: selectedChannel.active, channelAccess: (selectedChannel.active && this.isChannelSubscribed(selectedChannel.channel_name))}));
        }
        return true
    }
    onOpenChannelUsersDialog(e){
        this.setState({showChannelUsersDialog: true});
    }
    onCloseChannelUsersDialog(e){
        this.setState({showChannelUsersDialog: false});
    }
    onOpenDeleteChannelDialog(e){
        this.setState({showDeleteChannelDialog: true});
    }
    onCloseDeleteChannelDialog(e){
        this.setState({showDeleteChannelDialog: false});
    }
    onOpenCreateChannelDialog(e){
        this.setState({showCreateChannelDialog: true})
    }
    onCloseCreateChannelDialog(e){
        this.setState({showCreateChannelDialog: false, newChannelName: '', newChannelTopic: '', createChannelNameErrorState: false, createChannelTopicErrorState: false})
    }
    onOpenChannelTopicDialog(e){
        this.setState({showChannelTopicDialog: true})
    }
    onCloseChannelTopicDialog(e){
        this.setState({showChannelTopicDialog: false, changeChannelTopic: '', changeChannelTopicErrorState: false})
    }
    onCreateChannel(e){
        
        if(/\S/.test(this.state.newChannelName)){   
            let payload = {type: 'create', channel_name: this.state.newChannelName.trim(), channel_topic: this.state.newChannelTopic.trim(), user: this.state.user}
            fetch(window.location.href+'api/channels/', {
                method: 'POST',
                credentials: "same-origin",
                headers: {
                    "X-CSRFToken": get_cookie('csrftoken'),
                    "Accept": "application/json",
                    "Content-Type": "application/json"
                },
                body: JSON.stringify(payload)
            })
            .then(response => {
                if (response.status !== 200) {
                    return this.setState({ placeholder: "Fail to create channel" });
                }
                return response.json();
            })
            .then(data => {
                //console.log(data);
                if(data.success){
                    chat_socket.send(JSON.stringify({ type: 'add_channel',  user: this.state.user, channel_name: this.state.newChannelName }))
                    //console.log("Fetching local")
                    this.fetchChannels().then(done => {
                        return this.onSelectedChannel(null, data.channel_name, data.channel_url);
                    });
                    this.setState({showCreateChannelDialog: false, newChannelName: '', newChannelTopic: '', createChannelTopicErrorState: false})
                } else {
                    if(data.type == 'name_error'){
                        this.setState({createChannelNameErrorState: true, createChannelNameError: data.reason})
                    }
                    if(data.type == 'topic_error'){
                        this.setState({createChannelTopicErrorState: true, createChannelTopicError: data.reason})
                    }
                }
            });
            
        } else {
            this.setState({createChannelNameErrorState: true, createChannelNameError: 'Enter a channel name!'})
        }
    }
    onChangeChannelTopic(e){
        let payload = {type: 'change_topic', channel_name: this.state.activeChannel.channel_name, channel_topic: this.state.changeChannelTopic.trim(), user: this.state.user}
        fetch(window.location.href+'api/channels/', {
            method: 'POST',
            credentials: "same-origin",
            headers: {
                "X-CSRFToken": get_cookie('csrftoken'),
                "Accept": "application/json",
                "Content-Type": "application/json"
            },
            body: JSON.stringify(payload)
        })
        .then(response => {
            if (response.status !== 200) {
                return this.setState({ placeholder: "Fail to change topic" });
            }
            return response.json();
        })
        .then(data => {
            //console.log(data);
            if(data.success){
                chat_socket.send(JSON.stringify({ type: 'change_topic', channel_name: this.state.activeChannel.channel_name, user: this.state.user }))
                this.setState({showChannelTopicDialog: false, changeChannelTopic: '', changeChannelTopicErrorState: false})
            } else {
                if(data.type == 'topic_error'){
                    this.setState({changeChannelTopicErrorState: true, changeChannelTopicError: data.reason})
                }
            }
        });
    }
    onAutoComplete(suggestion, suggestionIndex, matches){
        this.setState({autocompleteValue: ''})
        var channel_url = matches[suggestionIndex].channel_url;
        //console.log("Channing socket to: "+ channel_url);
        change_socket(channel_url+'/');
        if(this.isChannelSubscribed(suggestion))
            this.onSelectedChannel(null, suggestion, channel_url)
        else
            this.setState({activeChannel: this.getChannelObject(suggestion), channelSelected: true, channelAccess: false})
    }
    onAutoCompleteChange(text, e){
        this.setState({autocompleteValue: text})
    }
    onButtonClick(e, type){
        if(type == 'Join'){
            // Fetch api
            const message_data = { type: 'join_channel', user: this.state.user};
            chat_socket.send(JSON.stringify(message_data));
            this.setState({channelAccess: true});
        }
        else if(type == 'Leave'){
            // Fetch
            const message_data = { type: 'leave_channel', user: this.state.user};
            chat_socket.send(JSON.stringify(message_data));
            this.setState({channelAccess: false});
        }
        else if(type == 'Delete'){
            const message_data = { type: 'delete_channel', user: this.state.user};
            chat_socket.send(JSON.stringify(message_data));
        }
    }
    onJoinChannel(channel_name){
        this.fetchChannels().then(data => {;
        this.setState({activeChannel: this.getChannelObject(channel_name)});
        })
    }
    onLeaveChannel(local){
        this.fetchChannels().then(data =>{
            if(local){
                this.setState({channelSelected: false, channelAccess: false, activeChannel: null, showDeleteChannelDialog: false});
            } else {
                this.setState(prevState => ({activeChannel: (prevState.activeChannel != null ? this.getChannelObject(prevState.activeChannel.channel_name) : null)}));
            }
        });
    }
    onMediaChange(type, media){
        let media_class = null;
        if(media.desktop){
            media_class = 'md-transition--deceleration md-title--permanent-offset'
        } else {
            media_class = ''
        }
        this.setState({mediaClass: media_class})
    }
    componentDidMount() {
        chat_socket.onopen = function(){
            //console.log("Connected to chat socket: Generic");
        }
        chat_socket.onclose = function(){
            //console.log("Disconnected from chat socket: Generic");
        }
        chat_socket.onmessage = function(m){
            var data = JSON.parse(m.data);
            //console.log("App.js:")
            //console.log(data.event);
            if(data.event == 'add_channel' || data.event == 'delete_channel'){
                //console.log("Fetching from websocket")
                this.fetchChannels();
            }
        }.bind(this)
        this.fetchUser().then(()=> {
            this.fetchChannels();
        });
    }
    render() {
        const {navItems, channelSelected, activeChannel, isLoading, channelAccess, mediaClass, 
            channels, autocompleteValue, 
            showCreateChannelDialog, showDeleteChannelDialog, showChannelUsersDialog, showChannelTopicDialog,
            createChannelNameError,createChannelTopicError, changeChannelTopicError, 
            createChannelNameErrorState, createChannelTopicErrorState, changeChannelTopicErrorState,
            newChannelName, newChannelTopic, changeChannelTopic,
             user} = this.state;
        const divStyle = {
            filter: 'blur(5px)',
            width: '100%',
            height: '90vh',
            pointerEvents: 'none'
          };
        const h3Style = {
            top: '32%',
            zIndex: '1',
            whiteSpace: 'normal',
            wordBreak: 'break-word',
            position: 'fixed',
        };
        const channelStyle = {
            fontWeight: '300',
            textOverflow: 'ellipsis',
            maxWidth: '85vw',
            overflow: 'hidden',
            whiteSpace: 'nowrap'
        }
        const nameStyle = {
            display: 'inline',
            marginRight: '8px',
            letterSpacing: '0',
            fontSize: '24px'
        }
        const ChatOptions = () => (
            <MenuButton
                id="menu-button-2"
                icon
                centered
                className={'md-btn md-btn--icon md-btn--hover md-pointer--hover md-inline-block md-btn--toolbar md-toolbar--action-right'}
                menuItems={[
                    <ListItem key={1} onClick={(e) => this.onOpenChannelUsersDialog(e)} primaryText="View People" />,

                    (activeChannel != null) && (activeChannel.creator != null) ? <ListItem key={3} onClick={(e) => this.onOpenChannelTopicDialog(e)} primaryText="Change Topic" /> : <div key={3}></div>,

                    (activeChannel != null) && (activeChannel.creator != null) && (user.username == activeChannel.creator.username) ? 
                    <ListItem key={2} onClick={(e) => this.onOpenDeleteChannelDialog(e)} primaryText="Delete Channel" /> :
                    (activeChannel != null) && (activeChannel.creator != null) ? <ListItem key={2} onClick={(e) => this.onButtonClick(e, "Leave")} primaryText="Leave Channel" /> : <div key={2}></div>

                ]}        
                position={Layover.Positions.BOTTOM_RIGHT}     
                >
                more_vert
            </MenuButton>
        );
        return (
            isLoading ? <div className={"loader"}>
            <svg viewBox="0 0 32 32" width="32" height="32">
              <circle id="spinner" cx="16" cy="16" r="14" fill="none"></circle>
            </svg>
          </div> : (
            <NavigationDrawer
              drawerId="main-navigation"
              drawerTitle="Let's Talk About It"
              toolbarId="main-toolbar"
              tabletDrawerType={NavigationDrawer.DrawerTypes.TEMPORARY}
              toolbarTitle={channelSelected && activeChannel != null ? '# '+activeChannel.channel_name +(activeChannel.topic != null && activeChannel.topic != '' ? " Topic: " + activeChannel.topic : "") : "Select a Channel or"}
              toolbarTitleStyle={channelStyle}
              navItems={navItems}
              onMediaTypeChange={(type, media) => this.onMediaChange(type, media)}
              toolbarChildren={channelAccess ? null : <Autocomplete
                                                            key={'search-channels'}
                                                            id={'search-channels'}
                                                            block
                                                            placeholder={mediaClass == '' ? '# Search': '# Search for a Channel'}
                                                            data={channels}
                                                            dataLabel={'channel_name'}
                                                            dataValue={'channel_name'}
                                                            toolbar
                                                            value={autocompleteValue}
                                                            filter={Autocomplete.caseInsensitiveFilter}
                                                            style={{marginLeft: '32px', maxWidth: '300px'}}
                                                            listStyle={{maxWidth: '300px'}}
                                                            onChange={(text, e) => this.onAutoCompleteChange(text, e)}
                                                            onAutocomplete={(suggestion, suggestionIndex, matches) => (this.onAutoComplete(suggestion, suggestionIndex, matches))}
                                                        />}
              toolbarActions={channelSelected ? (
                  channelAccess ? (<ChatOptions />) 
                    : (<Button onClick={(e) => this.onButtonClick(e, "Join")} flat primary swapTheming>Join Channel</Button>)) : null}
            >
            <DialogContainer
                id="create_channel_dialog"
                visible={showCreateChannelDialog}
                onHide={(e) => {(this.onCloseCreateChannelDialog(e))}}
                actions={[<Button flat primary onClick={(e) => this.onCreateChannel(e)}>Create</Button>]}
                title="Create Channel"
            >
                <TextField
                    id="channel-name"
                    label="Name"
                    placeholder="Channel name"
                    value={newChannelName}
                    error={createChannelNameErrorState}
                    errorText={createChannelNameError}
                    onChange={(value, e) => this.setState({newChannelName: value, createChannelNameError: '', createChannelNameErrorState: false})}
                />
                <TextField
                    id="channel-topic"
                    label="Topic (optional)"
                    maxLength={40}
                    placeholder="Channel Topic"
                    value={newChannelTopic}
                    error={createChannelTopicErrorState}
                    errorText={createChannelTopicError}
                    onChange={(value, e) => this.setState({newChannelTopic: value, createChannelTopicErrorState: false, createChannelTopicError: ''})}
                />
            </DialogContainer>

            <DialogContainer
                id="delete_channel_dialog"
                visible={showDeleteChannelDialog}
                onHide={(e) => {(this.onCloseDeleteChannelDialog(e))}}
                actions={[<Button flat primary onClick={(e) => this.onCloseDeleteChannelDialog(e)}>Cancel</Button>,
                        <Button flat secondary onClick={(e) => this.onButtonClick(e, 'Delete')}>Delete Channel</Button>]}
                title="Delete Channel?"
            />
            {activeChannel != null ? 
            <DialogContainer
                id="channel_users_dialog"
                visible={showChannelUsersDialog}
                onHide={(e) => {(this.onCloseChannelUsersDialog(e))}}
                title={"People in #"+ activeChannel.channel_name}
            >
                <List>
                {activeChannel.users.map((user, index) => 
                    <ListItem
                        key={index}
                        primaryText={user.username}
                        primaryTextStyle={nameStyle}
                        secondaryText={user.first_name + " " + user.last_name}
                        leftAvatar={ <Avatar style={{border: 'none', width: '52px', height: '52px', borderRadius: '10%'}} src={'https://avatars.io/instagram/'+user.username} />}
                    />)}
                </List>
            </DialogContainer>
            : null}

            {activeChannel != null ? 
            <DialogContainer
                id="channel_topic_dialog"
                visible={showChannelTopicDialog}
                onHide={(e) => {(this.onCloseChannelTopicDialog(e))}}
                actions={[<Button flat primary onClick={(e) => this.onChangeChannelTopic(e)}>Change</Button>]}
                title={"Topic"}
                aria-describedby="speed-boost-description"
            >
                <p id="speed-boost-description" className="md-color--secondary-text">{activeChannel.topic}</p>
                <TextField
                    id="channel-topic"
                    label="Change Topic"
                    maxLength={40}
                    placeholder="Channel Topic"
                    value={changeChannelTopic}
                    error={changeChannelTopicErrorState}
                    errorText={changeChannelTopicError}
                    onChange={(value, e) => this.setState({changeChannelTopic: value, changeChannelTopicErrorState: false, changeChannelTopicError: ''})}
                />
            </DialogContainer>
            : null}

                               {channelSelected && activeChannel != null ? (
                               channelAccess? (<Channel key={activeChannel.channel_name} mediaClass={mediaClass} user={user} channelAccess={channelAccess} 
                                                        channel={activeChannel} joinCallback={(channel_name) => this.onJoinChannel(channel_name)} leaveCallback={(local) => this.onLeaveChannel(local)}
                                                        endpoint={window.location.href+'api/'+activeChannel.channel_url+'/messages?page='} />)
                               : (
                                <div>
                                    <Grid style={{display: 'contents'}}>
                                        <Cell size={12} offset={mediaClass == '' ? 0 : 3}>
                                    <div className={'md-display-3'} style={h3Style}>Join <i style={{fontWeight: '200'}}># {activeChannel.channel_name}</i> to view messages </div>
                                    </Cell>
                                    </Grid>
                                    <div style={divStyle}>
                                        <Channel key={activeChannel.channel_name} mediaClass={mediaClass} user={user} channelAccess={channelAccess} 
                                                channel={activeChannel} joinCallback={(channel_name) => this.onJoinChannel(channel_name)} leaveCallback={(local) => this.onLeaveChannel(local)}
                                                endpoint={window.location.href+'api/'+activeChannel.channel_url+'/messages?page='} />
                                    </div>
                                </div>
                               )) : null}
            </NavigationDrawer>
            )
          );
    }
}
const wrapper = document.getElementById("app");
wrapper ? ReactDOM.render(<App />, wrapper) : null;
