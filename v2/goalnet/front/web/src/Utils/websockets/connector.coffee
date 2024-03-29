
export class DataSource
    constructor:({name, send_conn})->
        @name = name
        @send_conn = send_conn

    set_callback:(callback)=>
        if callback
            @onData = callback
            console.log 'set up ondata handler', @onData
        else
            console.log 'Trying to set source callback to ', callback

    send:(data)->
        packet:
            name:@name
            data:data
        console.log 'sending', packet
        @send_conn(JSON.stringify(packet))

    onData:(data)=>
        console.log 'No callback registered for', @name


export class Connector
    constructor:({api_path}) ->
        @api_path = api_path
        @callbacks = []

    connect:(api_path)->
        # if provided argument, update the api_path
        if api_path
            @api_path = api_path
        console.log 'Starting websocket connectiton to', @api_path
        @socket = new WebSocket(@api_path)
        @connected = false

        @socket.onmessage = (m)=> @onMessage(m)
        @socket.onopen  =  @onOpen
        @socket.onclose =  @onClose
        @socket.onerror =  @onError

    add_callback:(clb)=>
      @callbacks.push clb

    onMessage:(event)=>
        console.log 'WebSocket got', event
        message = JSON.parse(event.data)
        for clb in @callbacks
          clb message

    ####
    # A bunch of handlers with logging
    onOpen:()=>
        @connected = true
        console.log 'Websocket connected', @api_path
        @on_state_change('open')

    onClose:()=>
        @connected = false
        console.info 'Websocket closed', @api_path
        @on_state_change('closed')

    onError:(e)=>
        console.error 'Error from socket', e
        @on_state_change('error',e)
    ####

    on_state_change:(state, event)=>
        if @onStateChange
            @onStateChange state, event
    close:()=>
        console.log 'Closing socket to', @api_path
        @socket.close()
        
    send:(message)=>
        if @connected
            if typeof(message)=='object'
                message=JSON.stringify message
            @socket.send(message)
            console.debug('sent',message)
        else
            console.error('Websocket not connected')

    setOnStateChange:(event_callback)=>
        if not event_callback
            console.error 'Attempted to set onStateChange to ', event_callback
        @onStateChange = event_callback

export default class DataRouter extends Connector
    constructor:(props)->
        super(props)
        @sources = []

    callback:(message)=>
        {name,data} = message
        if @sources[name]
            console.log '@sources', @sources
            @sources[name].onData(data)
        else
            console.log 'Received data for unknown consumer', message

    get_source:(name)->
        source = new DataSource(name:name,send_conn:@send)
        @sources[name] = source
        source
