const HTMLWebpackPlugin = require("html-webpack-plugin");
const MiniCssExtractPlugin = require("mini-css-extract-plugin");
const { EsbuildPlugin } = require("esbuild-loader");

const path = require("path");

const config = {
  entry: {
    main: path.resolve(__dirname, "./src/index.tsx"),
  },
  context: path.resolve(__dirname, "./src"),
  output: {
    path: path.resolve(__dirname, "./dist"),
    filename: "bundle.js",
    publicPath: "/",
    clean: true,
  },
  resolve: {
    extensions: [".js", ".ts", ".tsx"],
    fallback: { fs: false, os: false, path: false },
    alias: {
      src: path.resolve(__dirname, "./src"),
    },
  },
  module: {
    rules: [
      {
        test: /\.jsx?$/,
        loader: "esbuild-loader",
        options: {
          loader: "jsx",
        },
        exclude: /node_modules/,
      },
      {
        test: /\.tsx?$/,
        loader: "esbuild-loader",
        exclude: /node_modules/,
      },
      {
        test: /\.css$/,
        use: [MiniCssExtractPlugin.loader, "css-loader"],
      },
      {
        test: /\.scss$/,
        use: [
          MiniCssExtractPlugin.loader,
          {
            loader: "css-loader",
            options: {
              modules: {
                auto: true,
                localIdentName: "[folder]-[local]__[hash:base64:7]",
                localIdentHashSalt: "accessioning",
              },
            },
          },
          "sass-loader",
        ],
      },
      {
        test: /\.svg$/i,
        issuer: /\.[jt]sx?$/,
        use: ["@svgr/webpack"],
      },
    ],
  },
};

module.exports = (env, argv) => {
  if (argv.mode === "production") {
    config.optimization = {
      minimize: true,
      minimizer: [
        new EsbuildPlugin({
          css: true,
        }),
      ],
    };
  }

  config.plugins ??= [];
  config.plugins.push(
    new MiniCssExtractPlugin({
      filename: "bundle.css",
      ignoreOrder: false,
    }),
    new HTMLWebpackPlugin({
      filename: "index.html",
      template: path.resolve(__dirname, "./src/index.html"),
      // inject: true,
    }),
  );

  if (argv.mode === "development") {
    config.devtool = "eval-source-map";
    config.devServer = {
      client: {
        overlay: {
          warnings: false,
          errors: true,
        },
      },
      port: 3000,
      hot: true,
      historyApiFallback: {
        index: "/",
      },
      static: {
        directory: path.resolve(__dirname, "./dist"),
      },
    };
  }

  return config;
};
