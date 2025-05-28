const connect_to_db = require('./db');
const talk = require('./Talk');

module.exports.get_by_id = async (event, context, callback) => {
    context.callbackWaitsForEmptyEventLoop = false;
    console.log('Received event:', JSON.stringify(event, null, 2));
    
    let body = {};
    if (event.body) {
        body = JSON.parse(event.body);
    }

    if (!body.id) {
        return callback(null, {
            statusCode: 500,
            headers: { 'Content-Type': 'text/plain' },
            body: 'Could not fetch the talks. ID is null.'
        });
    }

    try {
        await connect_to_db();
        console.log('=> get relatedVideos for talk');

        //Ricerca tramite ID, restituisce solo i relatedVideos
        const talkWatchNext = await talk.findOne({ _id: body.id }, { relatedVideos: 1, _id: 0})

        if (!talkWatchNext) {
            return callback(null, {
                statusCode: 404,
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ message: 'Talk not found.' })
            });
        }
        
        return callback(null, {
            statusCode: 200,
            body: JSON.stringify(talkWatchNext)
        });

    } catch (err) {
        console.error('Error fetching related videos:', err);
        return callback(null, {
            statusCode: err.statusCode || 500,
            headers: { 'Content-Type': 'text/plain' },
            body: 'Could not fetch the talks.'
        });
    }
};