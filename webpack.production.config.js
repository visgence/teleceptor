const path = require('path');
const webpack = require('webpack');
const BundleTracker = require('webpack-bundle-tracker');
const UglifyJSPlugin = require('uglifyjs-webpack-plugin'); // eslint-disable-line

module.exports = {
    entry: {
        app: './src/app.js',
        vendor: [
            'angular',
            'angular-route',
            'd3',
            'jquery',
            'angular-material',
            './node_modules/jstree/dist/jstree.min.js',
            './node_modules/angular-material/angular-material.min.css',
            './node_modules/adm-dtp/dist/ADM-dateTimePicker.min.css',
            './node_modules/adm-dtp/dist/ADM-dateTimePicker.min.js',
            './node_modules/font-awesome/css/font-awesome.min.css'
        ],
    },
    output: {
        filename: 'bundle-[chunkhash:8].js',
        path: path.resolve(__dirname, 'static/dist'),
    },
    devtool: false,
    module: {
        rules: [{
            test: /\.js$/,
            exclude: /node_modules/,
            loader: 'babel-loader',
            options: {
                presets: ['es2015'],
            },
        }, {
            test: /\.html$/,
            loader: 'html-loader',
        }, {
            test: /\.css$/,
            loader: 'style-loader!css-loader',
        }, {
            test: /\.scss$/,
            use: [{
                loader: 'style-loader',
            }, {
                loader: 'css-loader',
            }, {
                loader: 'sass-loader',
            }],
        }, {
            test: /\.png$|\?|\.gif($|\?)/,
            loader: 'url-loader?publicPath=/static/dist/&limit=100000',
        }, {
            test: /\.jpg$/,
            loader: 'file-loader',
        }, {
            test: /\.woff($|\?)|\.woff2($|\?)|\.ttf($|\?)|\.eot($|\?)|\.svg($|\?)/,
            loader: 'url-loader',
        }],
    },
    plugins: [
        new webpack.DefinePlugin({
            'process.env': {
                NODE_ENV: JSON.stringify('production'),
            }
        }),
        new BundleTracker({
            filename: './webpack-stats.json',
        }),
        new webpack.ProvidePlugin({
            jQuery: 'jquery',
            $: 'jquery',
            jquery: 'jquery',
        }),
        new webpack.LoaderOptionsPlugin({
            minimize: true,
            debug: false,
        }),
        new webpack.optimize.CommonsChunkPlugin({
            name: 'vendor',
            filename: 'vendor.bundle.js',
        }),
        new webpack.NamedModulesPlugin(),
        new webpack.optimize.UglifyJsPlugin({
            compress: {
                dead_code: true,
                drop_debugger: true,
                conditionals: true,
                comparisons: true,
                booleans: true,
                unused: true,
                toplevel: true,
                if_return: true,
                join_vars: true,
                cascade: true,
                collapse_vars: true,
                reduce_vars: true,
                warnings: false,
                drop_console: true,
                passes: 2
            },
            mangle: false
        }),
    ]
};
