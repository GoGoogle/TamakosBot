const tracer = require('tracer')
const fs = require('fs');

module.exports = tracer.console({
    transport: function (data) {
        console.log(data.output);
        fs.appendFile('./info.log', data.output + '\n', (err) => {
            if (err) throw err;
        });
    }
});

// logger.log('hello');
// logger.trace('hello', 'world');
// logger.debug('hello %s', 'world', 123);
// logger.info('hello %s %d', 'world', 123, { foo: 'bar' });
// logger.warn('hello %s %d %j', 'world', 123, { foo: 'bar' });
// logger.error('hello %s %d %j', 'world', 123, { foo: 'bar' }, [1, 2, 3, 4], Object);

