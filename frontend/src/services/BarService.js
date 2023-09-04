import BaseService from './BaseService'
import { httpClient } from './HttpClient'

class BarService extends BaseService {
  handleResponseJSONString(res) {
    if (!res) { // if key not exists, will return null
      return null
    }

    try {
      const result = JSON.parse(res.content)
      return result
    } catch (error) {
      throw new Error('Json parse error')
    }
  }

  postWebNote(key, value) {
    return this.post('/client/api/v2/webNotes', {
      key,
      content: JSON.stringify(value)
    }).then(this.handleResponseJSONString)
  }

  putWebNote(key, value) {
    return this.put('/client/api/v2/webNotes', {
      key,
      content: JSON.stringify(value)
    }).then(this.handleResponseJSONString)
  }

  getWebNote(key) {
    return this.get(`/client/api/v2/webNotes/${key}`).then(this.handleResponseJSONString)
  }
}

export default BarService

export const barService = new BarService(httpClient)