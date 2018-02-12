var path = require("path")
var webpack = require("webpack")
var BundleTracker = require("webpack-bundle-tracker")

module.exports = {
    context: __dirname,
    entry: {
        index: '../assets/js/index/index',
        result: '../assets/js/result/index',
    },

    output: {
        path: path.resolve('./static/bundles/'),
        filename: "[name].js"
    },

    module: {
        loaders: [
            //{ test: "/\.css$", loader: "style!css" },
            {
                test: /\.jsx?$/,
                exclude: /node_modules/,
                loader: 'babel-loader',
                 query: {
                   presets: ['es2016', 'es2015', 'react']
                }
            }, // to transform JSX into JS

            {
              test: require.resolve('jquery'),
              use: [
                { loader: 'expose-loader', options: 'jQuery' },
                { loader: 'expose-loader', options: '$' }
              ]
            },
        ]
    },

    resolve: {
        modules: ['node_modules', 'bower_components'],
        extensions: ['*', '.js', '.jsx']
    },

    plugins: [
        new BundleTracker({filename: './webpack-stats.json'}),
        //new ExtractTextPlugin("[name].css"),
        //new webpack.ProvidePlugin({$: "jquery", jQuery: "jquery"})
    ],

    watch: true, // auto rebuild if changed
};
