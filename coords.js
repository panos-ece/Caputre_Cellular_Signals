'use strict';

const bs = require('../lib/bscoords');
const sqlite3 = require('sqlite3').verbose();

let db = new sqlite3.Database('/root/cell_info.db', sqlite3.OPEN_READONLY, (err) => {
  if (err) {
    console.error(err.message);
  }
  console.log('Connected to my database.');
});

let db_coords = new sqlite3.Database('/root/coords.db',(err) => {
	if(err) {
		console.error(err.message);
	}
	console.log('Database coords created');
});

//db_coords.run('DROP TABLE IF EXISTS coords'); 
db_coords.run('CREATE TABLE IF NOT EXISTS coords(lat double, lon double, provider string, cell string, freq string, scan_lat double, scan_lon double)');

const services = ['opencellid'];

bs.init({
    apikey_opencellid: 'pk.6d18b1a25cb511b416c7ebc11b8ddac1',

    'timeout': 3000
});

db.serialize(() => {
  db.each(`SELECT mcc,mnc,lac,cell,imsioperator,freq,scan_lat,scan_lon
           FROM observations`, (err, row) => {
    if (err) {
      console.error(err.message);
    }
    
  
    if ((row.mcc != '') && (row.mcc != null)) {
	console.log(row);
    	bs
      	.opencellid(row.mcc,row.mnc,row.lac,row.cell)
      	.then(coords => {
        	console.log(coords);
 			db_coords.run(`INSERT INTO coords(lat, lon, provider, cell, freq, scan_lat, scan_lon) VALUES (?, ?, ?, ?, ?, ?, ?)`, 
					[coords.lat,coords.lon,row.imsioperator,row.cell,row.freq,row.scan_lat,row.scan_lon], function(err) {
		    	if (err) {
    		  		return console.log(err.message);
    			} 	
  			});
      	})
      	.catch(err => console.log(err));
    }
  });
});

db.close((err) => {
  if (err) {
    console.error(err.message);
  }
  console.log('Close the database connection.');
});

setTimeout(() => {  
	db_coords.close((err) => {
  	if (err) {
    	console.error(err.message);
  	}
  	console.log('Close the database connection.');
	});
}, 1000);



