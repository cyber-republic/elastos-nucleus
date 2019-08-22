import React, { Component } from "react";

import SyntaxHighlighter from "react-syntax-highlighter";
import { gruvboxDark } from "react-syntax-highlighter/dist/esm/styles/hljs";

import {
  Grid,
  Row,
  Col,
  FormGroup,
  ControlLabel,
  FormControl,
  Button
} from "react-bootstrap";

import { Card } from "components/Card/Card.jsx";
import axios from "axios";
import { baseUrl } from "../utils/api";

class UserProfile extends Component {
  constructor() {
    super();

    this.state = {
      inputs: {
        hashKey: "",
        apiKey: ""
      },
      output: ""
    };

    this.handleClick = this.handleClick.bind(this);
  }

  changeHandler = event => {
    const key = event.target.name;
    const value = event.target.value;

    this.setState({
      inputs: {
        ...this.state.inputs,
        [key]: {
          ...this.state.inputs[key],
          value
        }
      },
      output: ""
    });
  };

  verifyMessage() {
    const endpoint = "hive/showContent/";
    axios
      .get(baseUrl + endpoint + this.state.inputs.hashKey.value, {
        headers: {
          api_key: this.state.inputs.apiKey.value,
          "Content-Type": "application/json;"
        }
      })
      .then(response => {
        this.setState({
          output: response.data
        });
      })
      .catch(error =>
        this.setState({
          inputs: {
            hashKey: "",
            apiKey: ""
          },
          output: error
        })
      );
  }

  handleClick() {
    //TODO:
    //1.check for the api key
    if (this.state.inputs.apiKey.value !== undefined) {
      this.verifyMessage();
    } else {
      this.setState({
        output: "Please enter an API Key to proceed further"
      });
      console.log("api key not present");
    }
  }

  render() {
    return (
      <div className="content">
        <Grid fluid>
          <Row>
            <Col md={6}>
              <Card
                title="Show file contents using an API Key"
                content={
                  <form>
                    <Row>
                      <Col md={12}>
                        <FormGroup>
                          <ControlLabel>API Key</ControlLabel>
                          <FormControl
                            rows="3"
                            componentClass="textarea"
                            bsClass="form-control"
                            placeholder="Enter your API Key here"
                            name="apiKey"
                            value={this.state.inputs.apiKey.value}
                            onChange={this.changeHandler}
                          />
                          <br />
                          <ControlLabel>Hash Key</ControlLabel>
                          <FormControl
                            rows="3"
                            componentClass="textarea"
                            bsClass="form-control"
                            placeholder="Enter your hash key here"
                            name="hashKey"
                            value={this.state.inputs.hashKey.value}
                            onChange={this.changeHandler}
                          />
                          <br />
                          <Button
                            onClick={this.handleClick}
                            variant="primary"
                            size="lg"
                          >
                            Verify
                          </Button>
                        </FormGroup>
                      </Col>
                    </Row>
                    <div className="clearfix" />
                  </form>
                }
              />
            </Col>
            <Col md={6}>
              {this.state.output && (
                <Card
                  title="File content"
                  content={
                    <form>
                      <Row>
                        <Col md={12}>
                          <FormControl
                            rows="3"
                            componentClass="textarea"
                            bsClass="form-control"
                            name="output"
                            value={this.state.output}
                            readOnly
                          />
                        </Col>
                      </Row>
                      <div className="clearfix" />
                    </form>
                  }
                />
              )}
            </Col>
          </Row>
          <Row>
            <Col md={12}>
              <Card
                title="Documentation"
                content={
                  <form>
                    <Row>
                      <Col md={12}>
                        <FormGroup controlId="formControlsTextarea">
                          <p>
                            <span className="category" />
                            Shows the content for the requested hash key from
                            hive.
                          </p>
                        </FormGroup>
                        <SyntaxHighlighter
                          language="javascript"
                          style={gruvboxDark}
                        >
                          {`GET /api/1/hive/showContent/(string:'hash_key') HTTP/1.1
Host: localhost:8888

headers:{
    "api_key":564732BHU
}
`}
                        </SyntaxHighlighter>
                        <SyntaxHighlighter
                          language="javascript"
                          style={gruvboxDark}
                        >
                          {`HTTP/1.1 200 OK
Vary: Accept
Content-Type: Text

Hello World
`}
                        </SyntaxHighlighter>
                      </Col>
                    </Row>

                    <div className="clearfix" />
                  </form>
                }
              />
            </Col>
          </Row>
          <Row>
            <Col md={12}>
              <Card
                title="Code Snippet"
                content={
                  <form>
                    <Row>
                      <Col md={12}>
                        <SyntaxHighlighter language="jsx" style={gruvboxDark}>
                          {`    api_key = request.headers.get('api_key')
    api_status = validate_api_key(api_key)
    if not api_status:
      data = {"error message":"API Key could not be verified","status":401, "timestamp":getTime(),"path":request.url}
      return Response(json.dumps(data), 
        status=401,
        mimetype='application/json'
      )

    api_url_base = settings.GMU_NET_IP_ADDRESS + settings.HIVE_PORT + settings.SHOW_CONTENT + "{}"
    myResponse = requests.get(api_url_base.format(hash_key))
    return Response(myResponse, 
        status=200,
        mimetype='application/json'
      )

                          `}
                        </SyntaxHighlighter>
                      </Col>
                    </Row>

                    <div className="clearfix" />
                  </form>
                }
              />
            </Col>
          </Row>
        </Grid>
      </div>
    );
  }
}

export default UserProfile;
