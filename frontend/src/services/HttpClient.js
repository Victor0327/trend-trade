import axios from 'axios'

class HttpClient {
  constructor(options = {}) {
    options.agent = false;

    this._options =  options
    this.$client = this.createHttpClient(options)
  }

  createHttpClient(options) {
    let timeout = parseInt(options.timeout, 10)
    if (isNaN(timeout)) {
      timeout = 5000
    }

    const $http = axios.create({
      proxy: false,
      baseURL: this.getOptionsBaseURL(options),
      timeout: this.getOptionsTimeout(options),
      headers: this.getOptionsHeaders(options),
    })

    $http.interceptors.request.use(
      config => ({
        ...config,
      })
    )


    $http.interceptors.response.use(
      res => this.handleHttpResponse(res),
      err => {
        err.config = {
          ...err.config,
        }

        this.handleHttpErrorResponse(err)
      }
    )

    return $http
  }

  /* ------------------------------------------- */

  getOptionsTimeout(options) {
    const timeout = parseInt(options.timeout, 10)
    if (isNaN(timeout) || timeout <= 0) {
      return 5000
    }
    return timeout
  }

  getOptionsBaseURL(options) {
    if (!options.baseURL) {
      return undefined
    }

    return options.baseURL
  }

  getOptionsHeaders(options) {
    let optionsHeaders = {
      ...options.headers
    }
    if (options._ip) {
      optionsHeaders['X-Forwarded-For'] = options._ip
    }
    if (options._contentId) {
      optionsHeaders['X-client-fb-content-id'] = options._contentId
    }

    return optionsHeaders
  }
  /* ------------------------------------------- */

  handleHttpResponse(res) {
    return res
  }

  extractResponseError(resData) {
    const { code, message, msg } = resData
    if (code !== 0) {
      return {
        errorMessage: message || msg,
        errorCode: code
      }
    }

    return null
  }

  handleHttpErrorResponse(err) {
    return err
  }

  /* ------------------------------------------- */

  useRequestInterceptor(factory) {
    this.$client.interceptors.request.use(factory)
  }

  useResponseInterceptor(onSuccess, onError) {
    this.$client.interceptors.response.use(onSuccess, onError)
  }

  useErrorInterceptor(onError) {
    this.useResponseInterceptor(
      res => res,
      onError
    )
  }

  /* ------------------------------------------- */
  send(args) {
    return this.$client.request(args)
  }
}

const httpClient = new HttpClient({
  timeout: 10000,
  baseURL: '/',
})

export default HttpClient
export {
  httpClient
}