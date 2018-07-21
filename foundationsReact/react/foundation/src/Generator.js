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
	}

	createFields(json) {
		var jsonFields = json.actions.POST
		var fieldKeys = Object.keys(jsonFields)
		console.log(fieldKeys)
		var form = []

		for (let i = 0; i < fieldKeys.length; i++) {
			var fieldName = fieldKeys[i]
			var field = jsonFields[fieldName]

			if (field.type === 'string') {
				form.push(<input type="text"/>)
			}
			else if (field.type === 'password') {
				form.push(<input type="password"/>)
			}
			else if (field.type === 'boolean') {
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