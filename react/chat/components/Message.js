import React, {Component} from "react";
import PropTypes from "prop-types";
import Grid from 'react-md/lib/Grids/Grid';
import Cell from 'react-md/lib/Grids/Cell';
import Avatar from 'react-md/lib/Avatars/Avatar';
import Twemoji from 'react-emoji-render';
const moment = require('moment');

class Message extends Component{
    static propTypes = {
        mobile: PropTypes.bool.isRequired,
        data: PropTypes.object.isRequired
    };
    
    render(){
        const gridStyle = {
            wordBreak: 'break-word',
            paddingLeft: '16px', 
            paddingRight: '8px', 
        }
        const cellStyle = {
            marginTop: '0',
            marginLeft: '0'
        }
        const nameStyle = {
            display: 'inline',
            marginRight: '8px',
            letterSpacing: '0',
            fontSize: '24px'
        }
        const messageBox = {
            marginLeft: 'initial',
            marginRight: 'initial',
            width: '100%'
        }
        const Item = () => (
            <Grid style={gridStyle} noSpacing={true}>
                <Cell align={'top'} size={12}><div className="md-title md-font-bold" style={nameStyle}>{this.props.data.user.username}</div><div style={{display: 'inline'}} className="md-font-light">{moment(this.props.data.timestamp).fromNow()}</div></Cell>
                <Cell size={12} align={'top'} style={{fontSize: 'large'}}><Twemoji text={this.props.data.message} /></Cell>
            </Grid>
        );
        return(
            <Grid style={messageBox}>
                <Cell style={cellStyle} size={12}>
                    <Avatar style={{float: 'left', border: 'none', width: '52px', height: '52px', borderRadius: '10%'}} src={'https://avatars.io/instagram/'+this.props.data.user.username} />
                    <Item />
                </Cell>
            </Grid>
        );
    }
}


export default Message;