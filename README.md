<div align="center" id="top"> 

  &#xa0;

  <!-- <a href="https://od-scaler.netlify.app">Demo</a> -->
</div>

<h1 align="center">OD Scaler</h1>

<p align="center">
  <img alt="Github top language" src="https://img.shields.io/github/languages/top/raghulkrishna/od-scaler?color=56BEB8">

  <img alt="Github language count" src="https://img.shields.io/github/languages/count/raghulkrishna/od-scaler?color=56BEB8">

  <img alt="Repository size" src="https://img.shields.io/github/repo-size/raghulkrishna/od-scaler?color=56BEB8">

  <img alt="License" src="https://img.shields.io/github/license/raghulkrishna/od-scaler?color=56BEB8">

<img alt="Github issues" src="https://img.shields.io/github/issues/raghulkrishna/od-scaler?color=56BEB8" />

<img alt="Github forks" src="https://img.shields.io/github/forks/raghulkrishna/od-scaler?color=56BEB8" /> 

<img alt="Github stars" src="https://img.shields.io/github/stars/raghulkrishna/od-scaler?color=56BEB8" /> 
</p>

<!-- Status -->

<!-- <h4 align="center"> 
	🚧  od-scaler 🚀 Under construction...  🚧
</h4> 

<hr> -->

<!-- <p align="center">
  <a href="#dart-about">About</a> &#xa0; | &#xa0; 
  <a href="#sparkles-features">Features</a> &#xa0; | &#xa0;
  <a href="#rocket-technologies">Technologies</a> &#xa0; | &#xa0;
  <a href="#white_check_mark-requirements">Requirements</a> &#xa0; | &#xa0;
  <a href="#checkered_flag-starting">Starting</a> &#xa0; | &#xa0;
  <a href="#memo-license">License</a> &#xa0; | &#xa0;
  <a href="https://github.com/raghulkrishna" target="_blank">Author</a>
</p> -->

<br>

## :dart: About ##

Slack Bot for upscaling or downscaling resources in kubernetes namespaces

## :checkered_flag: Starting ##

```bash
# Add the repo
$ helm repo add od-scaler https://raghulkrishna.github.io/helm-charts

# install the helm chart
$ helm install od-scaler/od-scaler

```

## :dart: Setup ##

1. Create a Slack APP https://api.slack.com/authentication/basics

2. Get slack bot token

3. Enable slack event subscriptions https://api.slack.com/apis/connections/events-api

4. Create a secret like this

```bash
apiVersion: v1
kind: Secret
metadata:
  name: od-scaler
stringData:
  SLACK_BOT_TOKEN: xoxb-XXXXXX-XXXXX-XXXXX
  BOT_USER_ID: U03J0XXXXX
  BASIC_AUTH_USER:od-scaler
  BASIC_AUTH_PASSWORD: powmsgtrajn1h12
```

5. Set the secret name in values.yaml

6. Setup ingress for od-scaler in values.yaml

7. Set url in slack event subscription as https://od-dcaler:powmsgtrajn1h12@slackify.com/slack/events

## :dart: Usage ##

To upscale/dowscale  a namespace 

```
@Scaler upscale replica 2 (number of replica)
```

Select the namespaces to upscale


if your cluster has https://codeberg.org/hjacobs/kube-downscaler
you can skip the kube-downscaler to downscale 



## :memo: License ##

This project is under license from MIT. For more details, see the [LICENSE](LICENSE.md) file.

<a href="#top">Back to top</a>
