export default class BaseService {
  constructor($http) {
    if (!$http) {
      throw new Error('must provide service instance for Service')
    }
    this.$http = $http
    this.timeout = undefined
  }

  setTimeout(value) {
    const timeout = parseInt(value, 10)
    if (!isNaN(timeout) && timeout > 0) {
      this.timeout = timeout
    }
  }

  send(args) {
    const payload = this.timeout
      ? {
        timeout: this.timeout,
        ...args
      }
      : args

    return this.$http.send(payload)
  }

  get(url, args) {
    return this.send({
      url,
      ...args,
      method: 'get'
    })
  }

  post(url, data, args) {
    return this.send({
      url,
      ...args,
      data,
      method: 'post'
    })
  }

  put(url, data, args) {
    return this.send({
      url,
      ...args,
      data,
      method: 'put'
    })
  }

  del(url, args) {
    return this.send({
      url,
      ...args,
      method: 'delete'
    })
  }
}
