const path = require('path');
const webpack = require('webpack');
const BundleTracker = require('webpack-bundle-tracker');
const UglifyJSPlugin = require('uglifyjs-webpack-plugin'); // eslint-disable-line
const BundleAnalyzerPlugin = require('webpack-bundle-analyzer').BundleAnalyzerPlugin; // eslint-disable-line

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
            './node_modules/jstree/dist/themes/default/style.min.css',
            './node_modules/angular-material/angular-material.min.css',
            './node_modules/adm-dtp/dist/ADM-dateTimePicker.min.css',
            './node_modules/adm-dtp/dist/ADM-dateTimePicker.min.js',
        ],
    },
    output: {
        filename: 'bundle-[chunkhash:8].js',
        path: path.resolve(__dirname, 'static/dist'),
    },
    devtool: 'eval-cheap-module-source-map',
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
        new BundleAnalyzerPlugin(),
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
    ],
};
