Shader "Metacraft/Procedural Wall"
{
    Properties
    {
        _BaseColor ("Base Color", Color) = (0.55, 0.55, 0.55, 1)
        _LineColor ("Line Color", Color) = (0.12, 0.12, 0.12, 1)
        _TileScale ("Tile Scale", Float) = 6
        _LineWidth ("Line Width", Range(0.005, 0.2)) = 0.035
        _Roughness ("Roughness", Range(0, 1)) = 0.85
    }
    SubShader
    {
        Tags { "RenderType"="Opaque" }
        LOD 200

        CGPROGRAM
        #pragma surface surf Standard fullforwardshadows
        #pragma target 3.0

        fixed4 _BaseColor;
        fixed4 _LineColor;
        float _TileScale;
        float _LineWidth;
        float _Roughness;

        struct Input
        {
            float2 uv_MainTex;
            float3 worldPos;
        };

        void surf(Input IN, inout SurfaceOutputStandard o)
        {
            float2 grid = frac(IN.worldPos.xz * _TileScale);
            float line = step(grid.x, _LineWidth) + step(grid.y, _LineWidth);
            fixed4 color = lerp(_BaseColor, _LineColor, saturate(line));
            o.Albedo = color.rgb;
            o.Smoothness = 1.0 - _Roughness;
            o.Metallic = 0;
        }
        ENDCG
    }
    FallBack "Diffuse"
}
