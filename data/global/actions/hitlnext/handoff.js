//CHECKSUM:b114996dd66449094119f38bf4d31ea71aa924c26a3b1e7161ea54f972b36be1
const axios = require('axios')

/**
 * Creates an handoff for a given conversation. By default handoffs are unassigned, they can then be assigned to agents and resolved.
 *
 * @title Handoff
 * @category hitlnext
 * @description Transfers control of the conversation to an agent
 * @author Botpress, Inc.
 */
const escalate = async event => {
  const axiosConfig = await bp.http.getAxiosConfigForBot(event.botId, { localUrl: true })
  await axios.post(
    '/mod/hitlnext/handoffs',
    {
      userThreadId: event.threadId,
      userId: event.target,
      userChannel: event.channel
    },
    axiosConfig
  )
}

return escalate(event)
