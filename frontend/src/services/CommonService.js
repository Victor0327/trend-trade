import BaseService from './BaseService'
import { httpClient } from './HttpClient'

class CommonService extends BaseService {
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

}

export default CommonService

export const commonService = new CommonService(httpClient)