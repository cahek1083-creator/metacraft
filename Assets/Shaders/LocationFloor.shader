Shader "Metacraft/Location Floor"
{
    Properties
    {
        _ColorA ("Color A", Color) = (0.18, 0.22, 0.26, 1)
        _ColorB ("Color B", Color) = (0.08, 0.1, 0.12, 1)
        _GridScale ("Grid Scale", Float) = 4
    }
    SubShader
    {
        Tags { "RenderType"="Opaque" }
        LOD 150

        CGPROGRAM
        #pragma surface surf Standard
        #pragma target 3.0

        fixed4 _ColorA;
        fixed4 _ColorB;
        float _GridScale;

        struct Input
        {
            float3 worldPos;
        };

        void surf(Input IN, inout SurfaceOutputStandard o)
        {
            float2 cell = floor(IN.worldPos.xz * _GridScale);
            float checker = fmod(cell.x + cell.y, 2.0);
            o.Albedo = lerp(_ColorA.rgb, _ColorB.rgb, checker);
            o.Smoothness = 0.15;
            o.Metallic = 0;
        }
        ENDCG
    }
    FallBack "Diffuse"
}
