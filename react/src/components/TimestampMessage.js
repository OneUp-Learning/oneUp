import React, {Component} from "react";
import PropTypes from "prop-types";
import Grid from 'react-md/lib/Grids/Grid';
import Cell from 'react-md/lib/Grids/Cell';
import Avatar from 'react-md/lib/Avatars/Avatar';
import Twemoji from 'react-emoji-render';
const moment = require('moment');

class TimestampMessage extends Component{
    static propTypes = {
        mobile: PropTypes.bool.isRequired,
        data: PropTypes.object.isRequired
    };
    
    render(){
        const gridStyle = {
            wordBreak: 'break-word',
            paddingRight: '8px', 
        }
        const cellStyle = {
            margin: '0',
        }
        const nameStyle = {
            display: 'inline',
            marginRight: '8px',
            letterSpacing: '0',
            fontSize: '18px'
        }
        
        const messageBox = {
            marginLeft: 'initial',
            marginRight: 'initial',
            width: '100%'
        }
        
        return(
            <Grid style={messageBox}>
                <Cell style={cellStyle} size={12}>
                    <Grid style={gridStyle} noSpacing={true}>
                        <Cell align={'top'} size={12}>
                            <div className="md-title " style={nameStyle}>{this.props.data.value}</div>
                            <hr style={{borderColor: '#3f51b5', marginTop: '0'}} />
                        </Cell>
                    </Grid>
                </Cell>
            </Grid>
        );
    }
}


export default TimestampMessage;