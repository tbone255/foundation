import React from 'react';

export default class Generator extends React.Component {

	constructor(props) {
		super(props)
		
		this.state = {
			fields: this.getFields(),
			form: '',
		}

		
	}

	componentDidMount() {
		console.log('ye')
	}

	createFields(json) {
		var fields = json.fields
		var form = []

		for (let i = 0; i < fields.length; i++) {
			var field = fields[i]
			if (field.type === 'TextInput') {
				form.push(<input type="text"/>)
			}
			else if (field.type === 'CheckboxInput') {
				form.push(<input type="checkbox"/>)
			}
		}
		this.setState({form: form})
	}

	getFields() {
		try {
			fetch(this.props.url, {
			method: 'OPTIONS',
 		}).then((response) => response.json()).then((responseJson) => {this.createFields(responseJson)})
		}
		catch (e) {
			console.log(e)
		}
	}

	render() {

		return (
			<div>
				{this.state.form}
			</div>
		);
	}

}

// {
//     "fields": [
//         {
//             "class_name": "AutoField",
//             "name": "id"
//         },
//         {
//             "class_name": "CharField",
//             "name": "title",
//             "type": "TextInput"
//         },
//         {
//             "class_name": "BooleanField",
//             "name": "exists",
//             "type": "CheckboxInput"
//         }
//     ]
// }