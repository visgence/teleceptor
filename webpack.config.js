const path = require('path');
const webpack = require('webpack');
const BundleTracker = require('webpack-bundle-tracker');
const UglifyJSPlugin = require('uglifyjs-webpack-plugin'); // eslint-disable-line
const BundleAnalyzerPlugin = require('webpack-bundle-analyzer').BundleAnalyzerPlugin; // eslint-disable-line

// Note: Change this to NODE_ENV = Production
const isProd = false;

const plugins = [
    // new BundleAnalyzerPlugin(),
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
];

if (isProd) {
    plugins.push(
        new webpack.optimize.UglifyJsPlugin({
            compress: {
                warnings: false,
                screw_ie8: true,
                conditionals: true,
                unused: true,
                comparisons: true,
                sequences: true,
                dead_code: true,
                evaluate: true,
                if_return: true,
                join_vars: true,
            },
            output: {
                comments: false,
            },
        })
    )
}

module.exports = {
    entry: {
        app: './src/app.js',
        vendor: [
            'angular',
            'd3',
            'bootstrap',
            'jquery',
            'moment',
            'eonasdan-bootstrap-datetimepicker',
        ],
    },
    output: {
        filename: 'bundle-[chunkhash:8].js',
        path: path.resolve(__dirname, 'static/dist'),
    },
    devtool: isProd ? 'source-map' : 'eval-cheap-module-source-map',
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
            test: /bootstrap\/dist\/js\/umd\//,
            loader: 'imports?jQuery=jquery',
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
            test: /\.png$/,
            loader: 'url-loader?publicPath=/static/dist/&limit=100000',
        }, {
            test: /\.jpg$/,
            loader: 'file-loader',
        }, {
            test: /\.woff($|\?)|\.woff2($|\?)|\.ttf($|\?)|\.eot($|\?)|\.svg($|\?)/,
            loader: 'url-loader',
        }],
    },
    plugins: plugins,
};
