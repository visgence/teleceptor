const path = require('path');
const webpack = require('webpack');
const BundleTracker = require('webpack-bundle-tracker');
const UglifyJSPlugin = require('uglifyjs-webpack-plugin'); // eslint-disable-line
const BundleAnalyzerPlugin = require('webpack-bundle-analyzer').BundleAnalyzerPlugin; // eslint-disable-line

// Note: Change this to NODE_ENV = Production
const isProd = true;

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
    plugins.push(new webpack.optimize.UglifyJsPlugin({
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
    }));
    plugins.push(new webpack.DefinePlugin(
        'process.env': {
            NODE_ENV: JSON.stringify('production'),
        }
    ));
}

module.exports = {
    entry: {
        app: './src/app.js',
        vendor: [
            'angular',
            'angular-route',
            'd3',
            'bootstrap',
            'jquery',
            'angular-material',
            './node_modules/angular-material/angular-material.min.css',
            './node_modules/bootstrap/dist/css/bootstrap.min.css',
            './node_modules/adm-dtp/dist/ADM-dateTimePicker.min.css',
            './node_modules/adm-dtp/dist/ADM-dateTimePicker.min.js',
            './node_modules/bootstrap-treeview/dist/bootstrap-treeview.min.js'
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
