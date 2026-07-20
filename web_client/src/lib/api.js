const DEFAULT_API_BASE_URL = 'http://127.0.0.1:8010'

export const API_BASE_URL = (
  import.meta.env.VITE_API_BASE_URL?.trim() || DEFAULT_API_BASE_URL
).replace(/\/$/, '')

export function apiUrl(path) {
  const normalizedPath = path.startsWith('/') ? path : `/${path}`
  return `${API_BASE_URL}${normalizedPath}`
}

export async function fetchJson(path, options = {}) {
  const response = await fetch(apiUrl(path), options)
  const payload = await readJsonPayload(response)

  if (!response.ok) {
    throw new Error(extractErrorMessage(payload) || `Request failed with status ${response.status}.`)
  }

  return payload
}

export async function postJson(path, body) {
  return fetchJson(path, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  })
}

export async function streamJsonEvents(path, body, handlers = {}, requestOptions = {}) {
  const response = await fetch(apiUrl(path), {
    method: 'POST',
    headers: {
      Accept: 'text/event-stream',
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(body),
    ...requestOptions,
  })

  if (!response.ok) {
    const payload = await readJsonPayload(response)
    throw new Error(extractErrorMessage(payload) || `Stream request failed with status ${response.status}.`)
  }

  if (!response.body) {
    throw new Error('Streaming is not supported by this browser response.')
  }

  const reader = response.body.getReader()
  const decoder = new TextDecoder()
  let buffer = ''

  try {
    while (true) {
      const { done, value } = await reader.read()
      if (done) {
        break
      }

      buffer += decoder.decode(value, { stream: true }).replace(/\r/g, '')

      let separatorIndex = buffer.indexOf('\n\n')
      while (separatorIndex !== -1) {
        const rawMessage = buffer.slice(0, separatorIndex)
        buffer = buffer.slice(separatorIndex + 2)
        emitParsedEvent(rawMessage, handlers)
        separatorIndex = buffer.indexOf('\n\n')
      }
    }

    buffer += decoder.decode()
    if (buffer.trim()) {
      emitParsedEvent(buffer.replace(/\r/g, ''), handlers)
    }
  } finally {
    reader.releaseLock()
  }
}

async function readJsonPayload(response) {
  const text = await response.text()
  if (!text) {
    return {}
  }

  try {
    return JSON.parse(text)
  } catch {
    return { error: text }
  }
}

function emitParsedEvent(rawMessage, handlers) {
  if (!rawMessage.trim()) {
    return
  }

  let eventType = 'message'
  const dataLines = []

  for (const line of rawMessage.split('\n')) {
    if (!line || line.startsWith(':')) {
      continue
    }

    if (line.startsWith('event:')) {
      eventType = line.slice(6).trim()
      continue
    }

    if (line.startsWith('data:')) {
      dataLines.push(line.slice(5).trimStart())
    }
  }

  if (!dataLines.length) {
    return
  }

  const rawData = dataLines.join('\n')
  let payload

  try {
    payload = JSON.parse(rawData)
  } catch {
    payload = { event: eventType, delta: rawData }
  }

  const effectiveEvent = payload.event || eventType
  handlers.onEvent?.(payload)

  if (effectiveEvent === 'start') {
    handlers.onStart?.(payload)
  } else if (effectiveEvent === 'delta') {
    handlers.onDelta?.(payload)
  } else if (effectiveEvent === 'complete') {
    handlers.onComplete?.(payload)
  } else if (effectiveEvent === 'error') {
    handlers.onError?.(payload)
  }
}

function extractErrorMessage(payload) {
  if (!payload || typeof payload !== 'object') {
    return null
  }

  if (typeof payload.error === 'string' && payload.error.trim()) {
    return payload.error
  }

  if (typeof payload.message === 'string' && payload.message.trim()) {
    return payload.message
  }

  if (payload.response && typeof payload.response.error === 'string' && payload.response.error.trim()) {
    return payload.response.error
  }

  return null
}
