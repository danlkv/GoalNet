

mongoCred=process.env.MONGO_CREDENTIALS
module.exports={
	def_id:'5adcefbaed9d970d42d33d65',
//db:'mongodb://lykov.tech:27017/goalnet',
	db:"mongodb://"+mongoCred+
	"@localhost:27017/goalnet"
}
